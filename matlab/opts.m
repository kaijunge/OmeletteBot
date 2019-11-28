clear val
nvars=5;

gprMdl = fitrgp(KieranTotal,'output','KernelFunction','ardsquaredexponential',...
    'FitMethod','sr','PredictMethod','fic','Standardize',1);

%gprMdl = fitrgp(ATLogs2,'target','KernelFunction','ardsquaredexponential',...
%    'FitMethod','exact','PredictMethod','exact');
%
ypred = resubPredict(gprMdl);
% figure();
% plot(ATLogs.target,'r.');
% hold on
% plot(ypred,'b');
% xlabel('x');
% ylabel('y');
% legend({'data','predictions'},'Location','Best');


X= permn(1:10,nvars);
val = predict(gprMdl,X);

[~,I] = max(val);

Tot=X(I,:);

